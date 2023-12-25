 * \project	WonderTrader
 *
 * \author Wesley
 * \date 2020/03/30
 * 
 * \brief 
 */
#include "ParserAdapter.h"
#include "WtHelper.h"
#include "WtDtRunner.h"

#include "../Share/StrUtil.hpp"
#include "../Share/DLLHelper.hpp"
#include "../Share/StdUtils.hpp"
#include "../Share/CodeHelper.hpp"

#include "../Includes/WTSVariant.hpp"
#include "../Includes/WTSContractInfo.hpp"
#include "../Includes/WTSDataDef.hpp"
#include "../Includes/WTSVariant.hpp"

#include "../WTSTools/WTSBaseDataMgr.h"
#include "../WTSTools/WTSLogger.h"


//////////////////////////////////////////////////////////////////////////
//ParserAdapter
ParserAdapter::ParserAdapter(WTSBaseDataMgr * bgMgr, WtDtRunner* runner)
	: _parser_api(NULL)
	, _remover(NULL)
	, _stopped(false)
	, _bd_mgr(bgMgr)
	, _dt_runner(runner)
	, _cfg(NULL)
{
}

ParserAdapter::~ParserAdapter()
{
}

bool ParserAdapter::initExt(const char* id, IParserApi* api)
{
	if (api == NULL)
		return false;

	_parser_api = api;
	_id = id;

	if (_parser_api)
	{
		_parser_api->registerSpi(this);

		if (_parser_api->init(NULL))
		{
			ContractSet contractSet;
			WTSArray* ayContract = _bd_mgr->getContracts();
			WTSArray::Iterator it = ayContract->begin();
			for (; it != ayContract->end(); it++)
			{
				WTSContractInfo* contract = STATIC_CONVERT(*it, WTSContractInfo*);
				contractSet.insert(contract->getFullCode());
			}

			ayContract->release();

			_parser_api->subscribe(contractSet);
			contractSet.clear();
		}
		else
		{
			WTSLogger::log_dyn("parser", _id.c_str(), LL_ERROR, "[{}] Parser initializing failed: api initializing failed...", _id.c_str());
		}
	}

	return true;
}


bool ParserAdapter::init(const char* id, WTSVariant* cfg)
{
	if (cfg == NULL)
		return false;

	_id = id;

	if (_cfg != NULL)
		return false;

	_cfg = cfg;
	_cfg->retain();

	{
